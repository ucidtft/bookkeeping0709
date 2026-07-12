package com.yourapp.accountbook.ui.about

import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import androidx.fragment.app.Fragment
import com.yourapp.accountbook.R
import com.yourapp.accountbook.databinding.FragmentAboutBinding

class AboutFragment : Fragment() {
    private var _binding: FragmentAboutBinding? = null
    private val binding get() = _binding!!
    private var selectedSection = 0

    override fun onCreateView(inflater: LayoutInflater, container: ViewGroup?, savedInstanceState: Bundle?): View {
        _binding = FragmentAboutBinding.inflate(inflater, container, false)
        return binding.root
    }

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)
        showSection(0)

        binding.btnFeedback.setOnClickListener { showSection(0) }
        binding.btnAbout.setOnClickListener { showSection(1) }
        binding.btnVersion.setOnClickListener { showSection(2) }

        binding.tvVersionDetail.text = "当前版本: v" + try {
            requireContext().packageManager.getPackageInfo(requireContext().packageName, 0).versionName
        } catch (_: Exception) { "1.0.0" }
    }

    private fun showSection(index: Int) {
        selectedSection = index
        binding.btnFeedback.isSelected = index == 0
        binding.btnAbout.isSelected = index == 1
        binding.btnVersion.isSelected = index == 2
        binding.layoutFeedbackContent.visibility = if (index == 0) android.view.View.VISIBLE else android.view.View.GONE
        binding.layoutAboutContent2.visibility = if (index == 1) android.view.View.VISIBLE else android.view.View.GONE
        binding.layoutVersionContent2.visibility = if (index == 2) android.view.View.VISIBLE else android.view.View.GONE
    }


    override fun onDestroyView() {
        super.onDestroyView(); _binding = null
    }
}